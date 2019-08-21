# The depth level is used to to compute the cost in the right order.
# The highest level is 0, and it can go as deep as it can.
# You will have to compute the cost of the lowest level first and then go up to 0

module Process

  class SetEveItemDepthLevel

    def set

      Misc::Banner.p 'About to set eve item depth level'

      @min_level = 0

      @eve_items = Hash[ EveItem.all.map{ |e| [ e.id, e ] } ]

      @eve_items.values.each do |item|
        sub_set item, 1
      end

      EveItem.transaction do
        @eve_items.values.each do |item|
          item.save!
        end
      end

      File.open( 'data/lowest_production_level', 'w' ) do |f|
        f.write( @min_level )
      end

      Misc::Banner.p 'Eve item depth level set finished'
    end

    def sub_set( item, parent_level )
      item_level = item.production_level ? item.production_level : parent_level - 1
      item_level = [ item_level, parent_level - 1 ].min
      @min_level = [ item_level, @min_level ].min

      item.production_level = item_level

      materials = item.blueprint_materials

      if materials.empty?
        item.base_item = true
      else
        item.blueprint_materials.each do |m|
          sub_set @eve_items[m.eve_item_id], parent_level-1
        end
      end
    end

  end
end
