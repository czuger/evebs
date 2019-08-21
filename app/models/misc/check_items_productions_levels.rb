module Misc
  class CheckItemsProductionsLevels

    def check
      Misc::Banner.p 'Start checking productions levels'

      @failures = 0
      @logfile = File.open( 'log/items_productions_levels.err', 'w' )

      @eve_items = Hash[ EveItem.all.map{ |e| [ e.id, e ] } ]

      @eve_items.values.each do |item|
        next if item.base_item
        sub_check( item, 1, nil )
      end

      if @failures >= 1
        puts 'Failures found, please check logfile'
      else
        puts 'No failures found.'
      end

      @logfile.close

      Misc::Banner.p 'Productions levels check finished'
    end

    private

    def sub_check( item, parent_level, parent )
      unless item.production_level
        @logfile.puts "Production level for #{item.name}(#{item.id}) is null"
        @failures += 1
      else
        if item.production_level >= parent_level
          @logfile.puts "Production level for #{item.name}(#{item.id}) is over the parent's production level (#{parent.name}) : #{item.production_level} >= #{parent_level}"
          @failures += 1
        end
      end

      item.blueprint_materials.each do |ma|
        sub_item = @eve_items[ma.eve_item_id]
        next if sub_item.base_item
        sub_check( sub_item, item.production_level, item )
      end
    end

  end
end