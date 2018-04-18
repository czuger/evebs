class Station < ApplicationRecord
  belongs_to :trade_hub
  validates :trade_hub_id, :name, :cpp_station_id, presence: true

  def system
    trade_hub ? system.trade_hub : nil
  end

  def self.get_by_cpp_station_id(cpp_station_id)
    Station.where( 'cpp_station_id=?', cpp_station_id).first
  end

  def self.to_trade_hub_id(cpp_station_id)
    station = get_by_cpp_station_id(cpp_station_id)
    station && station.trade_hub ? station.trade_hub.id : nil
  end
end
