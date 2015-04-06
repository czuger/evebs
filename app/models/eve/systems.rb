$systems={
    Rens: 30002510,
    Pator: 30002544,
    Jita: 30000142,
    Hek: 30002053
}

class Eve::Systems
  def self.get_system_id api, station_name
    api.scope = "eve"
    # pp get_system_name( station_name )
    result = api.CharacterID(:names => get_system_name( station_name ) )
    # pp result
    raise "Systems#self.get_system_id unable to find station id for #{station_name}" unless result.characters.first.characterID
    result.characters.first.characterID
  end
  def self.get_system_name station_name
    station_name.split[0]
  end
end