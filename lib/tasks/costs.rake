namespace :data_compute do

  desc "Compute component costs from Jita prices - then refresh all items costs"
  task :costs => :environment do

    puts 'Recomputing costs from Jita prices'
    puts 'CAUTION : make sure that crest_prices_last_month_averages is loaded with Jita prices'
    Component.set_min_prices_for_all_components

    puts 'Refreshing all items costs'
    EveItem.where(involved_in_blueprint:true).all.each do |ei|
      puts "Recomputing cost for #{ei.name}"
      ei.compute_cost
    end
    puts 'End for all recomputing cost'
  end

end
