namespace :data_compute do
  desc "Recompute the costs for individual components"
  task :refresh_components_costs => :environment do
    unchecked_items = [ 235 ]
    # Refresh the prices if required
    puts 'Refreshing components costs'
    Component.all.to_a.each do |component|
      unless unchecked_items.include?( component.id )
        puts "Getting cost for #{component.id}, #{component.cpp_eve_item_id}, #{component.name}"
        component.set_min_price
      end
    end
  end
  desc "Recompute the costs for items"
  task :refresh_items_costs => :environment do
    puts 'Recomputing prices'
    EveItem.all.to_a.each do |ei|
      puts "Recomputing price for #{ei.name}"
      ei.compute_cost
    end
    puts 'End for recomputing cost'
  end
end
