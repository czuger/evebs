class Shared::Cost
  def self.by_name(name)
    COSTS.each_pair do |key,value|
      return value[:cost].to_f/value[:batch_size] if name==value[:name]
    end
    raise "Cost#by_name - #{name} price not known"
  end
  def self.by_id(id)
    raise "Cost#by_id - #{id} price not known" unless COSTS.has_key?(id)
    value = COSTS[id]
    return value[:cost].to_f/value[:batch_size]
  end
  def self.full_hash_by_id(id)
    raise "Cost#by_id - #{id} price not known" unless COSTS.has_key?(id)
    value = COSTS[id]
    return value
  end
  def self.types_ids
    COSTS.keys
  end
  COSTS={
    24531 =>{ id: 24531, cost: 14334014, batch_size: 50000, name:'Nova Fury Cruise Missile' },
    24533 =>{ id: 24533, cost: 14517051, batch_size: 50000, name:'Scourge Fury Cruise Missile' },
    24535 =>{ id: 24535, cost: 14333384, batch_size: 50000, name:'Mjolnir Fury Cruise Missile' },
    2621  =>{ id: 2621,  cost: 14445803, batch_size: 50000, name:'Inferno Fury Cruise Missile' },
    2637  =>{ id: 2637,  cost: 14445803, batch_size: 50000, name:'Inferno Precision Cruise Missile' },
    24537 =>{ id: 24537, cost: 14334014, batch_size: 50000, name:'Nova Precision Cruise Missile' },
    24539 =>{ id: 24539, cost: 14333384, batch_size: 50000, name:'Mjolnir Precision Cruise Missile' },
    24541 =>{ id: 24541, cost: 14517501, batch_size: 50000, name:'Scourge Precision Cruise Missile' },
    2817  =>{ id: 2817,  cost: 1804107 , batch_size: 50000, name:'Mjolnir Rage Rocket' },
    24471 =>{ id: 24471, cost: 1680228 , batch_size: 50000, name:'Scourge Rage Rocket' },
    24473 =>{ id: 24473, cost: 1661710 , batch_size: 50000, name:'Nova Rage Rocket' },
    24475 =>{ id: 24475, cost: 1692633 , batch_size: 50000, name:'Inferno Rage Rocket' },
    12787 =>{ id: 12787, cost: 6460470 , batch_size: 50000, name:'Null L' },
    9838  =>{ id: 9838,  cost: 1,        batch_size: 1,     name:'Superconductors' },
    202   =>{ id: 202,   cost: 2643991 , batch_size: 10000, name:'Mjolnir Cruise Missile' },
    203   =>{ id: 203,   cost: 14334014, batch_size: 10000, name:'Scourge Cruise Missile' },
    204   =>{ id: 204,   cost: 2024705 , batch_size: 10000, name:'Inferno Cruise Missile' },
    205   =>{ id: 205,   cost: 1335148 , batch_size: 10000, name:'Nova Cruise Missile' }
  }
end