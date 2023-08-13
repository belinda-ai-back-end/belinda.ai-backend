from enum import Enum
from fastapi import HTTPException
from typing import Union, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid

from belinda_app.models import Deal, StatusKeyEnumForCurator, StatusKeyEnumForMusician


class RoleEnum(str, Enum):
    curator = "curator"
    musician = "musician"


status_mapping: Dict[RoleEnum, Dict[str, Union[StatusKeyEnumForCurator, StatusKeyEnumForMusician]]] = {
    RoleEnum.curator: {
        "Confirm / Reject": StatusKeyEnumForCurator.confirm,
        "Confirmed, awaiting payment": StatusKeyEnumForCurator.confirmed_payment_curator,
        "Confirmed, awaiting placement": StatusKeyEnumForCurator.confirmed_placement_curator,
        "Placed - x days left until completion": StatusKeyEnumForCurator.payment_curator,
        "Completed, can be extended": StatusKeyEnumForCurator.completed_curator
    },
    RoleEnum.musician: {
        "Submit Application": StatusKeyEnumForMusician.submit,
        "Awaiting review": StatusKeyEnumForMusician.awaiting,
        "Confirmed, awaiting payment": StatusKeyEnumForMusician.confirmed_payment,
        "Confirmed, awaiting placement": StatusKeyEnumForMusician.confirmed_placement,
        "Placed - x days left until completion": StatusKeyEnumForMusician.payment,
        "Completed, can be extended": StatusKeyEnumForMusician.completed
    }
}


async def update_deal_status(
    session: AsyncSession,
    deal_id: str,
    role: RoleEnum,
    new_status: Union[StatusKeyEnumForCurator, StatusKeyEnumForMusician]
) -> None:
    try:
        deal_uuid = uuid.UUID(deal_id)
        deal = await session.get(Deal, deal_uuid)
        if deal is None:
            raise HTTPException(status_code=404, detail="Deal not found")
        if new_status not in status_mapping[role].values():
            raise HTTPException(status_code=400, detail="Invalid status for the given role")

        deal.status = new_status
        await session.commit()
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
