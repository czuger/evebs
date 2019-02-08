namespace :users_sales_orders do

  desc 'Show pending sales orders'
  task :show_pending_sales_orders => :environment do
    User.where( download_orders_running: true ).each do |user|
      p user
    end
  end

  desc 'Clear pending sales orders'
  task :clear_pending_sales_orders => :environment do
    User.where( download_orders_running: true ).update_all( download_orders_running: false )
  end

end

