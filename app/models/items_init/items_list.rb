require "yaml"

class ItemsInit::ItemsList

  def self.initialize_eve_items

    raise 'Do not use this method anymore'

    fixture_file = File.open('test/fixtures/eve_items.yml','a') if Rails.env.test?

    ActiveRecord::Base.transaction do
      list = download_items_list
      list.each do |elem|
        begin
          cpp_id = elem[0]
          name = I18n.transliterate( elem[1] )

          next if EveItem::UNPROCESSABLE_ITEMS.include?( cpp_id.to_i )

          eve_item = EveItem.to_eve_item_id( cpp_id )
          unless eve_item
            puts "About to insert #{elem.inspect}"
            eve_item = EveItem.find_or_create_by( cpp_eve_item_id: cpp_id, name: name, name_lowcase: name.downcase )

            if Rails.env.test?
              fixture = { "record#{ cpp_id }" => { cpp_eve_item_id: cpp_id, name: name, name_lowcase: name.downcase } }
              fixture_dump = YAML.dump( fixture )
              fixture_dump = fixture_dump[ 3..-1 ]
              fixture_file.puts( fixture_dump )
            end

          end

        rescue StandardError => e
          puts "Error with #{elem.inspect}"
        end

      end
    end
  end

  def self.involved_in_blueprint
    Blueprint.find_each do |bp|
      bp.materials.each do |material|
        comp = material.component
        eve_item = EveItem.where( cpp_eve_item_id: comp.cpp_eve_item_id, involved_in_blueprint: false ).first
        eve_item.update_attribute( :involved_in_blueprint, true ) if eve_item
      end
    end
  end

  def self.has_blueprint
    Blueprint.find_each do |bp|
      bp.eve_item.update_attribute( :involved_in_blueprint, true )
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