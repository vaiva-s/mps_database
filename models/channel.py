from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from models import Base

class DigitalChannel(Base):
  __tablename__ = 'digital_channels'
  id = Column(Integer, primary_key=True)
  number = Column(Integer, nullable=False) #NOTE: Channel numbers need to start at 0, not 1.
  card_id = Column(Integer, ForeignKey('application_cards.id'), nullable=False)
  device_input = relationship("DeviceInput", uselist=False, backref="channel")
  
class AnalogChannel(Base):
  __tablename__ = 'analog_channels'
  id = Column(Integer, primary_key=True)
  number = Column(Integer, nullable=False)
  card_id = Column(Integer, ForeignKey('application_cards.id'), nullable=False)
  analog_device = relationship("AnalogDevice", uselist=False, backref="channel")