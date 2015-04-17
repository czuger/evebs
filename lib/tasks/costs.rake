namespace :load do
  desc "Feed min prices per trade hubs"
  task :costs => :environment do
    EveItem.all.to_a.each do |eve_item|
      eve_item.update_attribute( :cost, 10 )
    end
  end
end
