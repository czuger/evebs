module Misc
  class CheckItemsProductionsLevels

    def check
      EveItem.each do |item|
        sub_monitor( item, nil, 0 )
        puts
      end
    end

    private

    def sub_check( item, req_qtt, level )
      puts ('%02d' % item.production_level) + ' > ' * level + " - #{item.name}(#{item.id}) - #{req_qtt} * #{item.cost ? item.cost : 'NULL'}"

      item.blueprint_materials.each do |ma|
        sub_monitor( ma.eve_item, ma.required_qtt, level+1 )
      end
    end

  end
end