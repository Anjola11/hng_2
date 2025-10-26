import httpx
from src.countries.models import Country, RefreshMetadata
import random 
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import DatabaseError
from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlmodel import select
from PIL import Image, ImageDraw, ImageFont
import os


class ExternalAPITasks:
    async def fetch_countries(self):
        url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(503, {
                "error": "External data source unavailable",
                "details": f"Could not fetch countries: {str(e)}"
            })
        
    async def fetch_exchange_data(self):
        url = "https://open.er-api.com/v6/latest/USD"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get('rates', {})
        except httpx.HTTPError as e:
            raise HTTPException(503, {
                "error": "External data source unavailable",
                "details": f"Could not fetch exchange rates: {str(e)}"
            })

        
class DbUpdateDataTasks(ExternalAPITasks):
    async def _generate_summary_image(self, countries_data, timestamp):
        """Generate summary image with country statistics"""
        try:
            # Sort countries by GDP (highest first)
            sorted_countries = sorted(
                [c for c in countries_data if c.get('estimated_gdp')],
                key=lambda x: x.get('estimated_gdp', 0),
                reverse=True
            )[:5]
            
            # Create blank image (800x600 white background)
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to load a nice font, fallback to default
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_normal = ImageFont.load_default()
            
            # Title
            y = 50
            draw.text((50, y), "Country Data Summary", fill='black', font=font_large)
            
            # Total countries
            y += 60
            draw.text((50, y), f"Total Countries: {len(countries_data)}", fill='black', font=font_normal)
            
            # Top 5 header
            y += 60
            draw.text((50, y), "Top 5 Countries by Estimated GDP:", fill='black', font=font_normal)
            
            # List top 5
            y += 40
            for i, country in enumerate(sorted_countries, 1):
                name = country['name']
                gdp = country.get('estimated_gdp', 0)
                text = f"{i}. {name}: ${gdp:,.2f}"
                draw.text((70, y), text, fill='blue', font=font_normal)
                y += 35
            
            # Timestamp
            y += 40
            draw.text((50, y), f"Last Refreshed: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}", 
                     fill='gray', font=font_normal)
            
            # Ensure cache directory exists
            os.makedirs('cache', exist_ok=True)
            
            # Save image
            img.save('cache/summary.png')
            
        except Exception as e:
            # Don't crash the whole refresh if image generation fails
            print(f"Warning: Could not generate summary image: {e}")

    async def add_countries(self, session: AsyncSession):
        try:
            countries = await self.fetch_countries()
            rates = await self.fetch_exchange_data()

            timestamp = datetime.now(timezone.utc)

            for country in countries:
                # Handle empty currencies
                country_currencies = country.get("currencies", [])
                country_currency_code = None
                
                if country_currencies:
                    country_first_currency = country_currencies[0]
                    country_currency_code = country_first_currency.get("code")
                
                # Get exchange rate
                country_exchange_rate = rates.get(country_currency_code) if country_currency_code else None
               
                # Calculate GDP
                if country_exchange_rate:
                    random_mult = random.uniform(1000, 2000)
                    estimated_gdp = (country['population'] * random_mult) / country_exchange_rate
                elif country_currency_code is None:
                    estimated_gdp = 0
                else:
                    estimated_gdp = None
                
                # Check if country exists
                statement = select(Country).where(Country.name.ilike(country['name']))
                result = await session.exec(statement)  
                existing_country = result.first()

                if existing_country:
                    # Update existing country
                    existing_country.capital = country.get('capital')
                    existing_country.region = country.get('region')
                    existing_country.population = country['population']
                    existing_country.currency_code = country_currency_code
                    existing_country.exchange_rate = country_exchange_rate
                    existing_country.estimated_gdp = estimated_gdp
                    existing_country.flag_url = country.get('flag')
                    existing_country.last_refreshed_at = timestamp
                
                else:
                    # Insert new country
                    new_country = Country(
                        name=country['name'],
                        capital=country.get('capital'),
                        region=country.get('region'),
                        population=country['population'],
                        currency_code=country_currency_code,
                        exchange_rate=country_exchange_rate,
                        estimated_gdp=estimated_gdp,
                        flag_url=country.get('flag'),
                        last_refreshed_at=timestamp
                    )
                    session.add(new_country)
            
            # Commit once
            await session.commit()

            # Update global metadata
            metadata_stmt = select(RefreshMetadata).where(RefreshMetadata.id == 1)
            metadata_result = await session.exec(metadata_stmt)
            metadata = metadata_result.first()

            if metadata:
                metadata.last_refreshed_at = timestamp
                metadata.total_countries = len(countries)
            else:
                metadata = RefreshMetadata(
                    id=1,
                    last_refreshed_at=timestamp,
                    total_countries=len(countries)
                )
                session.add(metadata)

            await session.commit()

            # Generate summary image
            await self._generate_summary_image(countries, timestamp)
        
            return {
                "message": "Countries refreshed successfully",
                "total_countries": len(countries),
                "timestamp": timestamp.isoformat()
            }
            
        except HTTPException:
            raise
        except DatabaseError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error"} 
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error"}
            )


    async def get_all_countries(self, 
                                region: str | None,
                                currency: str | None,
                                sort: str | None,
                                session: AsyncSession):
        statement = select(Country)

        # Apply filters
        if region is not None:
            statement = statement.where(Country.region.ilike(f"%{region}%"))
            
        if currency is not None:
            statement = statement.where(Country.currency_code.ilike(f"%{currency}%"))

        # Apply sorting
        if sort == 'gdp_desc':
            statement = statement.order_by(Country.estimated_gdp.desc())
        elif sort == 'gdp_asc':
            statement = statement.order_by(Country.estimated_gdp.asc())
        
        # Execute query
        result = await session.exec(statement)
        return result.all()
    
    async def get_refresh_status(self, session: AsyncSession):
        statement = select(RefreshMetadata).where(RefreshMetadata.id == 1)
        result = await session.exec(statement)
        return result.first()
    
    async def get_country_by_name(self, country_name: str, session: AsyncSession):
        try:
            
            statement = select(Country).where(Country.name.ilike(country_name))
            result = await session.exec(statement)
            country = result.first()

            
            if country:
                return country
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Country not found"}
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error"}
            )

    async def delete_country_by_name(self, name: str, session: AsyncSession):
        try:
            # Find country
            statement = select(Country).where(Country.name.ilike(name))
            result = await session.exec(statement)
            country_to_delete = result.first()

            # Check if exists
            if not country_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail={"error": "Country not found"}
                )
            
            # Delete country
            await session.delete(country_to_delete)
            await session.commit()
            
            return {"message": f"Country '{name}' deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error"}
            )
