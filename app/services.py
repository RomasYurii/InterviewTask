import httpx


async def verify_art_institute_place(external_id: int) -> bool:
    url = f"https://api.artic.edu/api/v1/artworks/{external_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.status_code == 200