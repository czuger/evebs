module Misc
  class MonitorUncomputedCosts

    def monitor
      EveItem.where( cost: Float::INFINITY ).each do |item|
        sub_monitor( item, nil, 0 )
        puts
      end
    end

    private

    def sub_monitor( item, req_qtt, level )
      puts ('%02d' % item.production_level) + ' > ' * level + " - #{item.name}(#{item.id}) - #{req_qtt} * #{item.cost}"

      item.blueprint_materials.each do |ma|
        sub_monitor( ma.eve_item, ma.required_qtt, level+1 )
      end
    end

  end
end