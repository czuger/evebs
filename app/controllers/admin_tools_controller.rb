class AdminToolsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity, :require_admin!, except: [ :denied ]

  def show
    @accounts_counts = User.count

    @user_log = {}
    @user_log_last_days = {}

    UserActivityLog.where.not( user: nil ).each do |ual|

      @user_log[ ual.user ] = 0 unless @user_log[ ual.user ]
      @user_log[ ual.user ] += 1

      @user_log_last_days[ ual.user ] = 0 unless @user_log_last_days[ ual.user ]
      @user_log_last_days[ ual.user ] += 1 if ual.updated_at > Time.now - ( 60*60*7)
    end
  end

  def min_prices_timings
    results = MinPricesLog.where( 'retrieve_start > ?', Time.now.to_date - 5 ).order( :retrieve_start )
      .pluck( :retrieve_start, :duration, :updated_items_count )

    times = results.map{|e| e[0].hour }
    duration = results.map{|e| e[1] }
    updated_items_count = results.map{|e| e[2] }

    @chart1 = LazyHighCharts::HighChart.new('graph') do |f|
      f.title(text: 'Min prices timings')
      f.xAxis(categories: times )
      f.series(name: 'Durations', yAxis: 0, data: duration, type: :spline )

      f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
      f.chart({defaultSeriesType: "column"})
    end

    @chart2 = LazyHighCharts::HighChart.new('graph') do |f|
      f.title(text: 'Min prices timings')
      f.xAxis(categories: times )
      f.series(name: 'Updated items count', yAxis: 0, data: updated_items_count, type: :spline )

      f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
      f.chart({defaultSeriesType: "column"})
    end

  end

  def activity
    total_request = "
      SELECT to_char(date_trunc('month', (created_at)), 'YYYY-MM'), count( * )
      FROM user_activity_logs
      GROUP BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')
      ORDER BY to_char(date_trunc('month', (created_at)), 'YYYY-MM')"

    total_result = UserActivityLog.connection.select_all( total_request )
    total_data = total_result.rows.map{ |e| e[ 1 ].to_i }
    total_categories = total_result.rows.map{ |e| e[ 0 ] }

    @chart = LazyHighCharts::HighChart.new('graph') do |f|
      f.title(text: "Connections")
      f.xAxis(categories: total_categories )
      f.series(name: "Total", yAxis: 0, data: total_data, type: :spline )

      f.legend(align: 'right', verticalAlign: 'top', y: 75, x: -50, layout: 'vertical')
      f.chart({defaultSeriesType: "column"})
    end

  end

  def denied
  end

end

