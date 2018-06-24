namespace :process do

  desc 'Download eve markets/histories'
  task :eve_markets_histories => :environment do
    Esi::DownloadPricesHistory.new( debug_request: false ).update_table
  end

  desc 'Compute prices history average'
  task :compute_prices_history_average => :environment do
    Crest::ComputePriceHistoryAvg.new
  end

  desc 'Compute component costs from Jita prices - then refresh all items costs'
  task :costs => :environment do
    EveItem.compute_cost_for_all_items
  end

  desc 'Dump eve_market_histories tp stream json'
  task :dump_eve_market_histories => :environment do
    File.open( '/tmp/eve_market_histories.json_stream', 'w' ) do |f|

      max = EveMarketHistoryArchive.count
      counter = 0
      start = Time.now

      EveMarketHistoryArchive.joins( :eve_item, :region ).find_each do |record|
        jr = {
            cpp_region_id: record.region.cpp_region_id.to_i, region_name: record.region.name, cpp_type_id: record.eve_item.cpp_eve_item_id,
            type_name: record.eve_item.name, year: record.year, month: record.month, history_date: record.history_date,
            order_count: record.order_count,
            volume: record.volume, low_price: record.low_price, avg_price: record.avg_price, high_price: record.high_price,
            created_at: record.created_at, updated_at: record.updated_at
        }

        f.puts( jr.to_json )

        counter += 1
        if counter % 100000 == 0

          current = Time.now
          elapsed = current - start
          p elapsed
          records_second = counter / elapsed
          full_job_time_in_sec = max / records_second
          eta = start + full_job_time_in_sec

          puts "#{counter}/#{max} - #{((counter*100.0)/max).round(2)}% - #{records_second.round} r/s - eta : #{eta}"
        end
      end
    end
  end

end