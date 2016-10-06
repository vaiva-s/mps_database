from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from models import Base

class DeviceState(Base):
  """
  DeviceState class (device_states table)

  Describe a state of a DigitalDevice, based on its value. 

  Properties:
    name: description of this state (e.g. BROKEN)
    value: the value a DigitalDevice should have to be in this state

  References:
    device_type_id: reference to the DeviceType that can be in this state

  Relationships:
    
    
  """
  __tablename__ = 'device_states'
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  value = Column(Integer, nullable=False)
  device_type_id = Column(Integer, ForeignKey('device_types.id'), nullable=False)
  digital_fault_states = relationship("DigitalFaultState", backref='device_state')
