import asyncio
import httpx
import random
from faker import Faker
from datetime import datetime
import json
import os
from typing import List, Dict, Optional, Any


class FakeDataGenerator:
    def __init__(self, base_url: str = "http://127.0.0.1:3333", admin_phone: str = "+998999999999",
                 admin_password: str = "admin"):
        self.faker = Faker()
        self.base_url = base_url
        self.admin_credentials = {"username": admin_phone, "password": admin_password}
        self.users = []
        self.mentors = []
        self.groups = []
        self.roles = ["admin", "mentor", "student"]
        self.admin_token = None

    async def get_admin_token(self) -> str:
        """Login as admin and return token"""
        if self.admin_token:
            return self.admin_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data=self.admin_credentials
            )

            if response.status_code != 200:
                raise Exception(f"Admin login failed: {response.text}")

            self.admin_token = response.json()["access_token"]
            return self.admin_token

    async def create_students(self, count: int = 80) -> List[Dict[str, Any]]:
        """Create fake users and store them in the instance"""
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        async with httpx.AsyncClient() as client:
            for i in range(count):
                user_data = {
                    "password": "123",
                    "email": self.faker.email(),
                    "phone": "+998" + random.choice(["90", "91", "93", "94", "88", "50", "51"]) +
                             "".join([str(random.randint(0, 9)) for _ in range(7)]),
                    "first_name": self.faker.first_name(),
                    "last_name": self.faker.last_name(),
                    "father_name": self.faker.first_name(),
                    "role": self.roles[2],
                    "student_id": self.faker.random_number(digits=6),
                    "group_id": random.choice([g["id"] for g in self.groups]) if self.groups else None,
                    "is_grant": random.choice([True, False]),
                    "course_number": random.randint(1, 4),
                    "attendance": random.randint(1, 100),
                    "academic": random.randint(1, 100),
                    "assignment": random.randint(1, 100),
                }

                response = await client.post(
                    f"{self.base_url}/user/student",
                    json=user_data,
                    headers=headers
                )

                if response.status_code == 200:
                    self.users.append(response.json())
                    print(f"Created student {i+1}/{count}: {user_data['first_name']}")
                else:
                    print(f"Failed to create student: {response.text}")
                
                await asyncio.sleep(0.05)

        return self.users


    async def create_mentors(self, count: int = 8) -> List[Dict[str, Any]]:
        """Create fake users and store them in the instance"""
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        async with httpx.AsyncClient() as client:
            for i in range(count):
                mentor_data = {
                    "password": "123",
                    "email": self.faker.email(),
                    "phone": "+998" + random.choice(["90", "91", "93", "94", "88", "50", "51"]) +
                             "".join([str(random.randint(0, 9)) for _ in range(7)]),
                    "first_name": self.faker.first_name(),
                    "last_name": self.faker.last_name(),
                    "father_name": self.faker.first_name(),
                    "role": self.roles[1],
                }

                response = await client.post(
                    f"{self.base_url}/user/mentor",
                    json=mentor_data,
                    headers=headers
                )

                if response.status_code == 200:
                    created_mentor = response.json()
                    self.mentors.append(created_mentor)
                    print(f"Created mentor: {mentor_data['first_name']}")
                else:
                    print(f"Failed to create mentor: {response.text}")

        return self.mentors


    async def update_mentor_group(self):
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        group_ids = [i["id"] for i in self.groups]
        
        async with httpx.AsyncClient() as client:
            for mentor in self.mentors:
                if not group_ids:
                    break
                
                mentor_id = mentor["user_id"]
                assigned_group_id = group_ids.pop(0)
                
                update_data = {
                    "group_ids": [assigned_group_id]
                }
                
                response = await client.put(
                    f"{self.base_url}/user/mentor/{mentor_id}",
                    json=update_data,
                    headers=headers
                )

                if response.status_code == 200:
                    print(f"Updated mentor ID {mentor_id} with group {assigned_group_id}")
                else:
                    print(f"Failed to update mentor {mentor_id}: {response.text}")


    async def create_groups(self, count: int = 8) -> List[Dict[str, Any]]:
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        mentor_ids = [u["user_id"] for u in self.mentors]

        async with httpx.AsyncClient() as client:
            for i in range(count):
                mentor_id = mentor_ids[i] if i < len(mentor_ids) else None
                group_data = {
                    "group_number": f"40{i+1}",
                    "mentor_id": mentor_id,
                }

                response = await client.post(
                    f"{self.base_url}/groups/",
                    json=group_data,
                    headers=headers
                )

                if response.status_code == 200:
                    created_group = response.json()
                    self.groups.append(created_group)
                    print(f"Created group: {group_data['group_number']}")
                else:
                    print(f"Failed to create group: {response.text}")

            return self.groups



async def main():
    # Example usage
    generator = FakeDataGenerator()


    await generator.create_mentors()
    await generator.create_groups()
    await generator.update_mentor_group()
    await generator.create_students()





if __name__ == "__main__":
    asyncio.run(main())