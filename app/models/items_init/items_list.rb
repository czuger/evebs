class ItemsInit::ItemsList

  def self.initialize_eve_items
    ActiveRecord::Base.transaction do
      list = download_items_list
      list.each do |elem|
        eve_item = EveItem.to_eve_item_id(elem[0])
        unless eve_item
          puts "About to insert #{elem.inspect}"
          EveItem.find_or_create_by( cpp_eve_item_id: elem[0], name: elem[1], name_lowcase: elem[1].downcase )
        end
      end
      Crest::MarketGroups.update_market_group
    end
  end

  private

  def self.download_items_list
    types = {}
    item_list = []
    open( 'http://eve-files.com/chribba/typeid.txt' ) do |file|
      file.readlines.each do |line|
        # pp line
        key = line[0..11]
        value = line[12..-3]
        # types[key.strip]=value.strip if value
        item_list << [key.to_i,value]
      end
    end
    item_list.shift(2)
    item_list.pop(3)
    item_list
  end

end