namespace :data_compute do

  desc "Get sales for me only"
  task :get_sales => :environment do

    puts '*'*100
    puts 'About to retrieve sales records'
    puts '*'*100

    SaleRecord.get_sale_records

    puts '*'*100
    puts 'Sales records retrieval finished'
    puts '*'*100
    puts

  end

end