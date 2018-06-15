class Esi::Errors::Base < RuntimeError

  def self.dispatch( exception )
    case exception.message
    when '504 Gateway Timeout'
      raise Esi::Errors::GatewayTimeout
    when '502 Bad Gateway'
      raise Esi::Errors::BadGateway
    when '403 Forbidden'
      raise Esi::Errors::Forbidden
    when '420 status code 420'
      raise Esi::Errors::ErrorLimited
    else
      raise exception
    end
  end

end