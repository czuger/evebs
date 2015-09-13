namespace :data_compute do
  desc "Retrieve all orders list for all users"
  task :get_orders => :environment do
    User.all.to_a.each do |user|
      puts "Retrieveing orders for #{user.name}"
      ActiveRecord::Base.transaction do
        TradeOrder.get_trade_orders(user)
      end
    end
  end
end