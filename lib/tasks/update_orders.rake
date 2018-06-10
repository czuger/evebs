namespace :process do

  desc "Retrieve all orders list for all users"
  task :get_orders => :environment do

    Esi::UpdateMyOrders.new.update

  end
end