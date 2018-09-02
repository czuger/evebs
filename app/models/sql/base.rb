module Sql
  class Base

    def self.update

      script_name = self.to_s[5..-1].underscore + '.sql'

      ActiveRecord::Base.transaction do
        Banner.p "About to run #{script_name}"

        request = File.open( "#{Rails.root}/sql/#{script_name}" ).read
        ActiveRecord::Base.connection.execute( request )
      end
    end

  end
end
