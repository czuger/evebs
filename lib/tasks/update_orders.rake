namespace :process do

  desc "Retrieve all orders list for all users"
  task :get_orders => :environment do
    Esi::UpdateMyOrders.new.update
  end

  desc "Retrieve all assets list for all characters"
  task :get_assets => :environment do
    Esi::DownloadMyAssets.new.update
  end

end