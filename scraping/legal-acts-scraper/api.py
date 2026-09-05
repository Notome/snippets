from datetime import datetime, timezone
from core.config import config
from aiohttp import FormData

from core import redis
import mimetypes
import secrets
import aiohttp


class Api:
    def __init__(self, token=None):
        self.token = token

        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    @staticmethod
    def get_external_id():
        return secrets.token_hex(16)

    async def get_user_info(self, external_id="my"):
        try:
            resp = await self.session.get(
                config.ORD_API_URL.format("v1", "person", external_id)
            )
        except Exception:
            return False

        if resp.status == 200:
            json = await resp.json()
            return json.get("name")

        return False

    async def create_creative(self, data, contract_id):
        external_id = self.get_external_id()
        media_external_ids = []

        for media_id in data["media_external_ids"]:
            _, id_ = media_id.split(":")
            media_external_ids.append(id_)

        data["media_external_ids"] = media_external_ids

        try:
            resp = await self.session.put(
                config.ORD_API_URL.format("v3", "creative", external_id), json=data
            )

            print("create_creative", await resp.text())

            if resp.status != 201:
                return False

            await redis.sadd(
                f"token:{self.token}:contract:{contract_id}:creatives", external_id
            )
        except Exception:
            return False

        return await resp.json()

    async def create_contract(self, data):
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        pads = []

        tmp = {
            "subject_type": "distribution",
            "type": data["contract_type"],
            "contractor_external_id": "",
            "flags": ["vat_included"],
            "client_external_id": "",
            "amount": data["cost"],
            "serial": date,
            "date": date,
        }

        for agent in data["agents"]:
            try:
                is_publisher, external_id = await self.create_person(agent)
            except Exception:
                return False

            if is_publisher:
                tmp["contractor_external_id"] = external_id

                for link in data["links"]:
                    pads.append(await self.create_pad(external_id, link))
            else:
                tmp["client_external_id"] = external_id

        try:
            contract_id = self.get_external_id()

            resp = await self.session.put(
                config.ORD_API_URL.format("v1", "contract", contract_id), json=tmp
            )

            print("create_contract", await resp.text())

            if resp.status != 201:
                return False

            await redis.sadd(f"token:{self.token}:contracts", contract_id)
            await redis.set(
                f"token:{self.token}:contract:{contract_id}",
                datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            )
            await redis.sadd(f"token:{self.token}:contract:{contract_id}:pads", *pads)

        except Exception:
            return False

        return True

    async def create_media(self, media_path, file_name):
        content_type, _ = mimetypes.guess_type(media_path)
        external_id = self.get_external_id()
        form = FormData()

        form.add_field(
            name="media_file",
            value=open(media_path, "rb"),
            filename=file_name,
            content_type=content_type,
        )

        try:
            del self.session.headers["Content-Type"]

            resp = await self.session.put(
                config.ORD_API_URL.format("v1", "media", external_id), data=form
            )

            print("create_media", await resp.text())

            if resp.status > 201:
                return False
        except Exception as e:
            print(e)
            return False

        return external_id

    async def create_person(self, person):
        persons = await redis.smembers(f"token:{self.token}:persons")
        inn = person["juridical_details"]["inn"]

        if inn in persons:
            external_id = await redis.get(f"token:{self.token}:person:{inn}")
        else:
            external_id = self.get_external_id()

            try:
                resp = await self.session.put(
                    config.ORD_API_URL.format("v1", "person", external_id), json=person
                )

                print("create_person", await resp.text())

                if resp.status != 201:
                    return False

                await redis.sadd(f"token:{self.token}:persons", inn)
                await redis.set(f"token:{self.token}:person:{inn}", external_id)
            except Exception:
                return False

        return "publisher" in person["roles"], external_id

    async def create_pad(self, owner_id, link):
        external_id = self.get_external_id()

        try:
            resp = await self.session.put(
                config.ORD_API_URL.format("v1", "pad", external_id),
                json={
                    "create_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "person_external_id": owner_id,
                    "name": external_id,
                    "is_owner": True,
                    "type": "web",
                    "url": link,
                },
            )

            print("create_pad", await resp.text())

            if resp.status != 201:
                return False

        except Exception:
            return False

        return external_id

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        if self.session:
            await self.session.close()
