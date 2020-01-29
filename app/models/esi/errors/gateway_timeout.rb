module Esi::Errors
  class GatewayTimeout < Base

    def pause
      sleep 60
    end

    def retry?
      true
    end

  end
end