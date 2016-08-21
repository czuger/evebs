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

    api.scope = 'eve'
    names = api.TypeName( ids: items.map{ |e| e.typeID }.join(',')).types
    names = Hash[ names.map{ |n| [ n.typeID, n.typeName ] } ]

    to_sell_items = items.map{ |a| { name: names[a.typeID], qtt: a.quantity.to_i, type_id: a.typeID } }
    pp to_sell_items

  end
end