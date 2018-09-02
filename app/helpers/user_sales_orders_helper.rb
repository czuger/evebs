module UserSalesOrdersHelper

  def trade_hub_from_hash_data( hash_data )
    "#{hash_data['trade_hubs.name']} (#{hash_data['regions.name']})"
  end
end