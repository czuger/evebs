namespace :process do

  desc 'Get daily sales for all items and trade hubs'
  task :get_sales_dailies => :environment do
    SalesDaily.compute_sold_amounts
  end

end