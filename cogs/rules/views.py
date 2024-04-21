from __future__ import annotations

from typing import Optional, TypeVar, TYPE_CHECKING

import discord
from discord import ui

from utils.enums import Roles

if TYPE_CHECKING:
    from bot import DevSocBot


RV = TypeVar("RV", bound="RulesView")


async def get_devsoc_role(
    itr: discord.Interaction[DevSocBot],
) -> Optional[discord.Role]:
    assert itr.guild

    role = itr.guild.get_role(Roles.DEVSOC)
    if not role:
        await itr.response.send_message(
            "Failed to retrieve the DevSoc role. Please contact an administrator",
            ephemeral=True,
        )
        return None

    return role


class AcceptButton(ui.Button[RV]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="I Accept",
            custom_id="accept_rules",
            emoji=discord.PartialEmoji(name="placement_yes", id=785695013525782578),
        )

    async def callback(self, itr: discord.Interaction[DevSocBot]) -> None:
        assert itr.guild and isinstance(itr.user, discord.Member)

        role = await get_devsoc_role(itr)
        if not role:
            return

        await itr.user.add_roles(role)
        await itr.response.send_message(
            "Welcome! You have been granted access to the DevSoc server!",
            ephemeral=True,
        )


class RulesView(ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

        self.add_item(AcceptButton())

    async def interaction_check(self, itr: discord.Interaction[DevSocBot]) -> bool:
        assert itr.guild and isinstance(itr.user, discord.Member)

        role = await get_devsoc_role(itr)
        if not role:
            return False

        if role in itr.user.roles:
            await itr.response.send_message(
                "You are already a member of the DevSoc server", ephemeral=True
            )
            return False

        return True
