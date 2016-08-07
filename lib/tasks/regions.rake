namespace :data_setup do
  desc "Feed regions list and link them to trade hubs (run data_setup:trade_hubs first)"
  task :regions => :environment do
    puts 'About to create regions an link them to trade hubs'

    c = Crest::InitRegions.new
    c.fill_regions

  end
end