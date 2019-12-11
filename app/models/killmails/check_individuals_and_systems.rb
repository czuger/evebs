require 'open-uri'
require 'json'
require 'pp'
require 'yaml'
require 'set'

module Killmails
  class CheckIndividualsAndSystems

    INDIVIDUALS = [ 2112875566, 96200467, 91808281, 93915289 ]
    SYSTEMS = [ 30000013, 30001398, 30002756 ]
    DB_FILE = 'tmp/old_killmails.yaml'

    def find
      requests = []
      INDIVIDUALS.each do |i|
        request = open( "https://zkillboard.com/api/kills/characterID/#{i}/" )
        requests += JSON.parse( request.read )
        sleep 1

        request = open( "https://zkillboard.com/api/losses/characterID/#{i}/" )
        requests += JSON.parse( request.read )
        sleep 1
      end

      SYSTEMS.each do |i|
        request = open( "https://zkillboard.com/api/solarSystemID/#{i}/" )
        requests += JSON.parse( request.read )
      end

      puts "#{requests.count} killmails to check"

      analyze_killmails requests
    end

    private

    def analyze_killmails( requests )
      load_db

      puts "#{requests.count} individuals to check"

      requests.each do |r|
        r = OpenStruct.new( r )
        # r.zkb = OpenStruct.new( r.zkb )

        next if @old_db.include?( r.killmail_id )

        e = Esi::Download.new( "killmails/#{r.killmail_id}/#{r.zkb['hash']}/", {}, debug_request: false )
        page = OpenStruct.new( e.get_page )
        page.killmail_time = DateTime.parse( page.killmail_time )

        if page.killmail_time > Time.now.to_datetime.gmtime - 1.hours
          # p page

          page.attackers.each do |attacker|
            e = Esi::Download.new( "characters/#{attacker['character_id']}/", {}, debug_request: false )

            next unless attacker['character_id']

            character = OpenStruct.new( e.get_page )
            name = character.name

            e = Esi::Download.new( "universe/systems/#{page.solar_system_id}/", {}, debug_request: false )
            system_data = OpenStruct.new( e.get_page )
            system_name = system_data.name

            time = page.killmail_time.localtime
            puts "#{name} spotted in #{system_name} at #{time}"
          end
        else
          # puts "#{page.killmail_id} too old : #{page.killmail_time}"
          # p page.killmail_id
          # p @old_db
          @old_db << page.killmail_id
          # p @old_db
        end
      end

      save_db
    end

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