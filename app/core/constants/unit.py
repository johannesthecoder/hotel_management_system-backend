from ..models.unit import UnitModel


class WeightUnit:
    KG = UnitModel(name="kg", value=1000)
    GRAM = UnitModel(name="gram", value=1)


class VolumeUnit:
    LITER = UnitModel(name="liter", value=1000)
    MILLILITER = UnitModel(name="milliliter", value=1)
    REGULAR_TEA_CUP = UnitModel(name="regular tea cup", value=300)
    JUICE_GLASS = UnitModel(name="milliliter", value=350)


class CountUnit:
    PIECE = UnitModel(name="piece", value=1)
    TRAY = UnitModel(name="tray", value=30)
    DOZEN = UnitModel(name="dozen", value=12)
    SAUSAGE_PACK = UnitModel(name="sausage pack", value=22)
