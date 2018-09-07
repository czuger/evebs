module Sql
  class Base

    def self.execute
      load_request do |request, script_name|
        ActiveRecord::Base.connection.execute( request  )
      end
    end

    def self.update( *params )
      load_request do |request, script_name|
        ActiveRecord::Base.connection.exec_update( request, script_name, params.map{ |p| [ nil, p ] } )
      end
    end

    private

    def self.load_request

      script_name = self.to_s[5..-1].underscore + '.sql'

      ActiveRecord::Base.transaction do
        Banner.p "About to run #{script_name}"

        request = File.open( "#{Rails.root}/sql/#{script_name}" ).read
        yield request, script_name
      end

    end
  end
end
