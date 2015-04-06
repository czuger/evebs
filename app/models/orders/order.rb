require 'pp'

# TODO : we will need to invalidate the cache frop open-uri-cached i think
# TODO : Simple remove of the tmp/api.eve-central.com directory
EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )

class Orders::Order
  constructor :api, :station, :type_name, :type_id, :price, :amount, :accessors => true
  def <=> order
    [station, type_name] <=> [order.station, order.type_name]
  end
  def display_array
    [ result, @type_name, system, "#{price_min} ISK", "#{@price} ISK", "#{cost} ISK", "#{@amount} Units", "#{benef} %", "#{marge_brute} MISK" ]
  end
  def system
    Eve::Systems.get_system_name(@station)
  end
  private
  # For colors, see : http://kpumuk.info/ruby-on-rails/colorizing-console-ruby-script-output/
  # Don't forget the \ before the e
  def result
    result = "\e[32mPrice ok\e[0m"
    result = "\e[31mPrice challenged !!\e[0m" if price_min && price_min < @price
    result
  end
  def benef
    ( ( @price * 100 ) / cost ).round(0) - 100 if cost
  end
  def marge_brute
    ( ( @price - cost ) * 50000 ) / 1000000.0 if cost
  end
  def cost
    Cost.by_name(@type_name)
  end
  def price_min
    system_id = Eve::Systems.get_system_id( @api, @station )
    raise "Unable to find system_id for #{@station}" unless system_id
    Orders::PriceWatcher.do( @type_id, system_id )
  end
end