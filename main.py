from pydantic import BaseModel
from typing import Dict, List, Type, TypeVar
import json

# ======================
# WSPÓLNE NARZĘDZIA
# ======================

def load_json(file_path: str):
    with open(file_path, 'r') as file:
        return json.load(file)


T = TypeVar('T', bound=BaseModel)


class JsonLoadable(BaseModel):

    @classmethod
    def load_list(cls: Type[T], file_path: str) -> List[T]:
        data = load_json(file_path)
        assert isinstance(data, list), f"Expected list for {cls.__name__}"
        return [cls(**item) for item in data]

    @classmethod
    def load_dict(cls: Type[T], file_path: str) -> Dict[str, T]:
        data = load_json(file_path)
        assert isinstance(data, dict), f"Expected dict for {cls.__name__}"
        return {key: cls(**value) for key, value in data.items()}


# ======================
# MODELE
# ======================

class Room(BaseModel):
    name: str
    area_m2: float


class Apartment(JsonLoadable):
    key: str
    name: str
    location: str
    area_m2: float
    rooms: Dict[str, Room]


class Tenant(JsonLoadable):
    name: str
    apartment: str
    room: str
    rent_pln: float
    deposit_pln: float
    date_agreement_from: str
    date_agreement_to: str


class Transfer(JsonLoadable):
    amount_pln: float
    date: str
    settlement_year: int | None
    settlement_month: int | None
    tenant: str


class Bill(JsonLoadable):
    amount_pln: float
    date_due: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str


class ApartmentSettlement(JsonLoadable):
    amount_pln: float
    description: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str


# ======================
# PARAMETRY
# ======================

class Parameters(BaseModel):
    apartments_json_path: str = 'data/apartments.json'
    tenants_json_path: str = 'data/tenants.json'
    transfers_json_path: str = 'data/transfers.json'
    bills_json_path: str = 'data/bills.json'
    apartment_settlement_json_path: str = 'data/apartmentsettlement.json'


# ======================
# MANAGER
# ======================

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters

        self.apartments = Apartment.load_dict(parameters.apartments_json_path)
        self.tenants = Tenant.load_dict(parameters.tenants_json_path)
        self.transfers = Transfer.load_list(parameters.transfers_json_path)
        self.bills = Bill.load_list(parameters.bills_json_path)
        self.apartment_settlements = ApartmentSettlement.load_list(
            parameters.apartment_settlement_json_path
        )


# ======================
# MAIN
# ======================

if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    for apartment in manager.apartments.values():
        print(apartment.key, apartment.name, apartment.location, apartment.area_m2)

        for room in apartment.rooms.values():
            print('  ', room.name, room.area_m2)

        for bill in manager.bills:
            if bill.apartment == apartment.key:
                print('  ', bill.amount_pln, bill.date_due,
                      bill.settlement_year, bill.settlement_month, bill.type)

    for tenant in manager.tenants.values():
        print(tenant.name, tenant.apartment, tenant.room,
              tenant.rent_pln, tenant.deposit_pln,
              tenant.date_agreement_from, tenant.date_agreement_to)

        for transfer in manager.transfers:
            if transfer.tenant == tenant.name:
                print('  ', transfer.amount_pln, transfer.date,
                      transfer.settlement_year, transfer.settlement_month)