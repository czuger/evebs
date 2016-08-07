class MigrationToPg::Migrate

  def self.migrate

    ActiveRecord::Base.connection.tables.each do |table_name|
      next if table_name == 'schema_migrations'

      puts "\n" + table_name
      ActiveRecord::Base.connection.columns(table_name).each {|c| puts "- " + c.name + ": " + c.type.to_s + " " + c.limit.to_s}
    end

  end

end