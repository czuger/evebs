namespace :data_compute do

  desc "Get sales for me only"
  task :get_sales => :environment do

    puts '*'*50
    puts 'About to retrieve sales records'
    puts '*'*50

    SaleRecord.get_sale_records

    puts '*'*50
    puts 'Sales records retrieval finished'
    puts '*'*50

  end

end