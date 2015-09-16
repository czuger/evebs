namespace :data_setup do

  desc "Feed trade hubs list"
  task :trade_hubs => :environment do
    puts 'About to create trade hubs'
    Setup::TradeHubs.new
  end

end