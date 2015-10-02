module ItemsInit::ItemSetupAndCompSelf

  def compute_min_price_for_system(system, items)
    # For now, we no more use the min price, but the avg prices
    # Method keep the old name, to avoid huge code refactoring

    prices = get_prices( system.eve_system_id, items.map{ |e| e.cpp_eve_item_id }, 'min' )

    prices.each do |cpp_item_id,price|
      # item = EveItem.find_by_cpp_eve_item_id( cpp_item_id )
      # puts "About to update price for #{item.name}"
      # We are cheating, the price is avg, but we still use the name min price
      if price # Sometime nobody sell this object
        item = EveItem.find_by_cpp_eve_item_id( cpp_item_id )
        item.set_min_price_for_system(price,system.id)
      end
    end

  end

  # Required for setting up the database
  def compute_all_costs
    types = {}
    item_list = []
    open( 'http://eve-files.com/chribba/typeid.txt' ) do |file|
      file.readlines.each do |line|
        # pp line
        key = line[0..11]
        value = line[12..-3]
        # types[key.strip]=value.strip if value
        item_list << [key.to_i,value] unless UNPROCESSABLE_ITEMS.include?(key.to_i)
      end
    end
    item_list.shift(2)
    item_list.pop(3)
    Hash[item_list]
  end

end