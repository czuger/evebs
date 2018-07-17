class AdminToolsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity, :require_admin!, except: [ :denied ]

  # def show
  #   @accounts_counts = User.count
  #
  #   request = 'SELECT "user", count( * ) cnt FROM user_activity_logs GROUP BY "user" ORDER BY count( * ) DESC'
  #   @users_log = UserActivityLog.connection.select_all( request ).to_a
  #   @users_log.sort_by!{ |x| x['cnt'].to_i }
  #   @users_log.reverse!
  #
  #   request = 'SELECT "user", count( * ) cnt FROM user_activity_logs WHERE created_at > current_date - interval \'7 days\' GROUP BY "user" ORDER BY count( * ) DESC'
  #   @users_log_last_days = UserActivityLog.connection.select_all( request ).to_a
  #   @users_log_last_days.sort_by!{ |x| x['cnt'].to_i }
  #   @users_log_last_days.reverse!
  # end
  #
  # def items_users
  #   request = 'SELECT "name", count( * ) FROM users, eve_items_users WHERE "users"."id" = user_id
  #     GROUP BY "name" ORDER BY count( * ) DESC'
  #   @users_log = UserActivityLog.connection.select_all( request ).to_a
  # end
  #
  # def crest_price_history_update
  #   datas = Caddie::CrestPriceHistoryUpdateLog.order( :feed_date ).to_a
  #   timeline = datas.map{ |e| e.feed_date }
  #
  #   charts_titles = [ [ 'Feeding time', 'Duration (in seconds)', :feeding_time ],
  #     [ 'Planning preprocess time', 'Duration (in seconds)', :update_planning_time ],
  #     [ 'Insertions', 'Insertions', :total_inserts ], [ 'Connections per seconds', 'Co/s', :co_seconds ] ]
  #
  #   @charts = []
  #
  #   charts_titles.each do |title_array|
  #     chart = LazyHighCharts::HighChart.new('graph') do |f|
  #       f.title(text: title_array[0])
  #       f.xAxis(categories: timeline )
  #       f.series(name: title_array[1], yAxis: 0, data: datas.map{ |e| e.send( title_array[2] ) } )
  #
  #       f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
  #       # f.chart({defaultSeriesType: "column"})
  #     end
  #     @charts << chart
  #   end
  # end
  #
  # def min_prices_timings_overview
  #   request = "SELECT to_char(date_trunc('day', (retrieve_start)), 'YYYY-MM-DD') update_day, count( * ) daily_runs,
  #     sum( duration ) total_duration, sum( updated_items_count ) total_updated_items
  #     FROM min_prices_logs
  #     GROUP BY to_char(date_trunc('day', (retrieve_start)), 'YYYY-MM-DD')
  #     ORDER BY to_char(date_trunc('day', (retrieve_start)), 'YYYY-MM-DD')"
  #
  #   timeline = []
  #   daily_runs = []
  #   total_duration = []
  #   total_updated_items = []
  #
  #   overview = MinPricesLog.connection.select_all( request )
  #   overview.each do |row|
  #     timeline << row['update_day']
  #     daily_runs << row['daily_runs'].to_i
  #     total_duration << row['total_duration'].to_i
  #     total_updated_items << row['total_updated_items'].to_i
  #   end
  #
  #   charts_titles = [ [ 'Total duration', 'Duration (in seconds)', total_duration ],
  #                     [ 'Total updated items', 'Updated items', total_updated_items ],
  #                     [ 'Daily runs', 'Runs', daily_runs ] ]
  #
  #   @charts = []
  #
  #   charts_titles.each do |title_array|
  #     chart = LazyHighCharts::HighChart.new('graph') do |f|
  #       f.title(text: title_array[0])
  #       f.xAxis(categories: timeline )
  #       f.series(name: title_array[1], yAxis: 0, data: title_array[2] )
  #
  #       f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
  #       # f.chart({defaultSeriesType: "column"})
  #     end
  #     @charts << chart
  #   end
  #
  # end
  #
  # def min_prices_timings
  #   results = MinPricesLog.where( 'retrieve_start > ?', Time.now.to_date - 5 ).order( :retrieve_start )
  #     .pluck( :retrieve_start, :duration, :updated_items_count )
  #
  #   times = results.map{|e| e[0].strftime( '%d|%H' ) }
  #   duration = results.map{|e| e[1] }
  #   updated_items_count = results.map{|e| e[2] }
  #
  #   @chart1 = LazyHighCharts::HighChart.new('graph') do |f|
  #     f.title(text: 'Min prices timings')
  #     f.xAxis(categories: times )
  #     f.series(name: 'Durations (en secondes)', yAxis: 0, data: duration )
  #
  #     f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
  #     # f.chart({defaultSeriesType: "column"})
  #   end
  #
  #   @chart2 = LazyHighCharts::HighChart.new('graph') do |f|
  #     f.title(text: 'Updated items count')
  #     f.xAxis(categories: times )
  #     f.series(name: 'Updated items count', yAxis: 0, data: updated_items_count )
  #
  #     f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
  #     # f.chart({defaultSeriesType: "column"})
  #   end
  # end
  #
  # def activity
  #   total_request = "
  #     SELECT to_char(date_trunc('month', (created_at)), 'YYYY-MM'), count( * )
  #     FROM user_activity_logs
  #     GROUP BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')
  #     ORDER BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')"
  #
  #   total_result = UserActivityLog.connection.select_all( total_request )
  #   total_data = total_result.rows.map{ |e| e[ 1 ].to_i }
  #   total_categories = total_result.rows.map{ |e| e[ 0 ] }
  #
  #   empty_connection_request = "
  #   SELECT to_char(date_trunc('month', (created_at)), 'YYYY-MM'), count( * )
  #   FROM user_activity_logs
  #   WHERE \"user\" IS NULL
  #   GROUP BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')
  #   ORDER BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')"
  #
  #   empty_result = UserActivityLog.connection.select_all( empty_connection_request )
  #   empty_data = empty_result.rows.map{ |e| e[ 1 ].to_i }
  #   empty_categories = empty_result.rows.map{ |e| e[ 0 ] }
  #
  #   @chart = LazyHighCharts::HighChart.new('graph') do |f|
  #     f.title(text: "Connections")
  #     f.xAxis(categories: total_categories )
  #     f.series(name: "Total", yAxis: 0, data: total_data )
  #     f.series(name: 'Unconnected', yAxis: 0, data: empty_data )
  #
  #     f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
  #     # f.chart({defaultSeriesType: "column"})
  #   end
  #
  # end
  #
  # def denied
  # end

end

