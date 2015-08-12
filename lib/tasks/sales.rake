namespace :data_compute do

  desc "Get sales for me only"
  task :get_sales => :environment do

    puts 'About to retrieve sales records'

    SaleRecord.get_sale_records

  end

end