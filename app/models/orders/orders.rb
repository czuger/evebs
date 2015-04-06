# https://github.com/3rdpartyeve/eaal

class Orders::Orders
  attr_reader :orders
  def initialize
    stations = Eve::Stations.new
    types = Eve::Types.new

    api = EAAL::API.new("3808229", "BHgPtSRlWR3cMsSadewgfE8UAAf2jhvT4Vvdo5f4JMyLTemqOzPMVMtch4Ww9ZJj")

    api.scope = "char"
    orders = api.MarketOrders(:characterID => 1866432960).orders.reject{ |e| e.orderState != '0' }

    @orders = orders.map{ |order|
      # pp order
      # puts "Checking order for #{types.name(order.typeID)} in #{stations.name(order.stationID)}"
      Orders::Order.new(
        api: api,
        station: stations.name(order.stationID),
        type_name: types.name(order.typeID),
        type_id: order.typeID,
        price: order.price.to_i,
        amount: order.volRemaining.to_i ) }.sort
  end
end


# api.scope = "eve"
# result = api.CharacterID(:names => "Gomex")
# puts result.characters.first.characterID # 1866432960