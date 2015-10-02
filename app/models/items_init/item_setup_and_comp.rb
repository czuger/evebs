module ItemsInit::ItemSetupAndComp

  def compute_cost
    total_cost = 0
    materials.each do |material|
      if material.component.cost
        total_cost += material.component.cost * material.required_qtt
      else
        puts "Warning !!! #{material.component.inspect} has no cost"
        # If we lack a material we set the price to nil and exit
        update_attribute(:cost,nil)
        return
      end
    end
    if total_cost <= 0
      puts "Warning !!! #{self.inspect} has no cost"
      # If we lack a material we set the price to nil and exit
      update_attribute(:cost,nil)
      return
    end
    update_attribute(:cost,total_cost)
  end

  def set_min_price_for_system(min_price,system_id)
    assert(min_price, "min_price is nil", self.class, __method__ )
    assert(system_id, "system is nil", self.class, __method__ )

    puts "Updating price for #{name}, price = #{min_price}"

    min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', id, system_id ).first
    unless min_price_item
      MinPrice.create!( eve_item: self, trade_hub_id: system_id, min_price: min_price )
    else
      min_price_item.update_attribute( :min_price, min_price )
    end
  end

end