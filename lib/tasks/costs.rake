namespace :data_compute do

  # desc "Recompute the costs for individual components"
  # task :refresh_components_costs => :environment do
  #   unchecked_items = [ 235 ]
  #   # Refresh the prices if required
  #   puts 'Refreshing components costs'
  #   Component.used_components.each do |component|
  #     unless unchecked_items.include?( component.id )
  #       puts "Getting cost for #{component.id}, #{component.cpp_eve_item_id}, #{component.name}"
  #       component.set_min_price
  #     end
  #   end
  # end

  desc "Retrieve all avg costs for all materials (not only used ones - avg prices from Jita)"
  task :retrieve_all_components_costs => :environment do
    puts 'Refreshing all components costs'
    Component.set_min_prices_for_all_components
  end

  # desc "Recompute the costs for items"
  # task :refresh_items_costs => :environment do
  #   puts 'Recomputing prices'
  #   EveItem.used_items.each do |ei|
  #     puts "Recomputing price for #{ei.name}"
  #     ei.compute_cost
  #   end
  #   puts 'End for recomputing cost'
  # end

  desc "Recompute the costs all items (not only used ones)"
  task :recompute_all_items_costs => :environment do
    puts 'Refreshing all items components costs'
    EveItem.where(involved_in_blueprint:true).all.each do |ei|
      puts "Recomputing price for #{ei.name}"
      ei.compute_cost
    end
    puts 'End for all recomputing cost'
  end

end
