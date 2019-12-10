require 'open-uri'
require 'json'
require 'pp'
require 'yaml'
require 'set'

module Killmails
  class CheckIndividualsAndSystems

    INDIVIDUALS = [ 2112875566, 96200467, 91808281, 93915289 ]
    SYSTEMS = [ 30000013, 30001398 ]
    DB_FILE = 'tmp/old_killmails.yaml'

    def find_individuals
      load_db

      requests = []
      INDIVIDUALS.each do |i|
        request = open( "https://zkillboard.com/api/kills/characterID/#{i}/" )
        requests += JSON.parse( request.read )
        sleep 1

        request = open( "https://zkillboard.com/api/losses/characterID/#{i}/" )
        requests += JSON.parse( request.read )
        sleep 1
      end

      puts "#{requests.count} individuals to check"

      requests.each do |r|
        r = OpenStruct.new( r )
        # r.zkb = OpenStruct.new( r.zkb )

        next if @old_db.include?( r.killmail_id )

        e = Esi::Download.new( "killmails/#{r.killmail_id}/#{r.zkb['hash']}/", {}, debug_request: false )
        page = OpenStruct.new( e.get_page )
        page.killmail_time = DateTime.parse( page.killmail_time )

        if page.killmail_time > Time.now - 1.hours
          p page
        else
          puts "#{page.killmail_id} too old : #{page.killmail_time}"
          # p page.killmail_id
          # p @old_db
          @old_db << page.killmail_id
          # p @old_db
        end
      end

      save_db
    end

    def check_systems
      load_db

      requests = []
      INDIVIDUALS.each do |i|
        request = open( "https://zkillboard.com/api/kills/characterID/#{i}/" )

        json_result = request.read
        requests += JSON.parse( json_result )
      end

      puts "#{requests.count} individuals to check"

      requests.each do |r|
        r = OpenStruct.new( r )
        # r.zkb = OpenStruct.new( r.zkb )

        next if @old_db.include?( r.killmail_id )

        e = Esi::Download.new( "killmails/#{r.killmail_id}/#{r.zkb['hash']}/", {}, debug_request: false )
        page = OpenStruct.new( e.get_page )
        page.killmail_time = DateTime.parse( page.killmail_time )

        if page.killmail_time > Time.now - 1.hours
          p page
        else
          puts "#{page.killmail_id} too old : #{page.killmail_time}"
          # p page.killmail_id
          # p @old_db
          @old_db << page.killmail_id
          # p @old_db
        end
      end

      save_db
    end

    private

    def load_db
      Misc::Banner.p 'DB loaded'
      @old_db = ( File.file?( DB_FILE ) ? YAML.load_file( DB_FILE ) : Set.new )
    end

    def save_db
      File.open( DB_FILE, 'w' ) do |f|
        f.write( @old_db.to_yaml )
      end

      Misc::Banner.p 'DB saved'
    end


  end
end