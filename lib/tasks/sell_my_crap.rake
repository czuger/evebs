namespace :extra_tools do

  desc "Sell my crap"
  task :sell_my_crap => :environment do

    EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )

    user = User.find( 4 )
    puts 'Using : ' + user.name
    api = EAAL::API.new( user.key_user_id, user.api_key )
    api.scope = 'account'
    pp api.Characters.characters.map{ |c| [ c.characterID, c.name ] }
    # pp characters.characters
    character_id = 95952305 # Barnard Tapie

    api.scope = 'char'
    assets = api.AssetList(:characterID => character_id )
    locations = assets.assets.map{ |e| e.locationID }.uniq
    puts "Locations = #{locations}"

    location = 60010729
    puts "Using location : #{location}"

    items = assets.assets.select{ |e| e.locationID == "#{location}" if e.respond_to?( 'locationID' ) }

    # api.scope = 'eve'
    # names = api.TypeName( ids: items.map{ |e| e.typeID }.join(',')).types
    # names = Hash[ names.map{ |n| [ n.typeID, n.typeName ] } ]
    # to_sell_items = items.map{ |a| { name: names[a.typeID], qtt: a.quantity.to_i, type_id: a.typeID } }

    results = []
    items.each do |item|
      i = EveItem.find_by_cpp_eve_item_id( item.typeID.to_i )
      if i
        prices = i.prices_advices.where.not( vol_month: nil ).
          order( '( min_price * least( vol_month/5, full_batch_size ) ) DESC NULLS LAST' )
        # puts prices.to_sql
        price = prices.first
        if price
          results_for_item = [ "#{i.name} - (#{i.id})", "#{price.trade_hub.name} - (#{price.trade_hub_id})",
                               price.vol_month.round( 0 ), price.min_price.round( 2 )]
          results_for_item << ( price.min_price - price.single_unit_cost ).round( 2 )
          results << results_for_item
        else
          puts "Nothing for #{i.name}"
        end
      end
    end
    results.sort_by!{ |e| e[1] }
    results.each do |results_for_item|
      padded_str = ( '%-50s'*2 + '%25s'*3 ) % results_for_item
      puts padded_str
    end
  end
end