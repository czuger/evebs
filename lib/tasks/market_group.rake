namespace :data_setup do
  desc "Setup market groups"
  task :market_groups => :environment do
    MarketGroups.update_market_group
  end
end