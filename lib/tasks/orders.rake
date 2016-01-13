namespace :data_compute do
  desc "Retrieve all orders list for all users"
  task :get_orders => :environment do

    puts '*'*100
    puts 'About to retrieve all orders list for all users'
    puts '*'*100

    User.all.to_a.each do |user|
      ActiveRecord::Base.transaction do
        TradeOrder.get_trade_orders(user)
      end
    end

    puts '*'*100
    puts 'End of retrieving all orders list for all users'
    puts '*'*100
    puts

  end
end