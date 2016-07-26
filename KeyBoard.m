function varargout = KeyBoard(varargin)
% KEYBOARD MATLAB code for KeyBoard.fig
%      KEYBOARD, by itself, creates a new KEYBOARD or raises the existing
%      singleton*.
%
%      H = KEYBOARD returns the handle to a new KEYBOARD or the handle to
%      the existing singleton*.
%
%      KEYBOARD('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in KEYBOARD.M with the given input arguments.
%
%      KEYBOARD('Property','Value',...) creates a new KEYBOARD or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before KeyBoard_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to KeyBoard_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help KeyBoard

% Last Modified by GUIDE v2.5 25-Jul-2016 23:00:51

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @KeyBoard_OpeningFcn, ...
    'gui_OutputFcn',  @KeyBoard_OutputFcn, ...
    'gui_LayoutFcn',  [] , ...
    'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before KeyBoard is made visible.
function KeyBoard_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to KeyBoard (see VARARGIN)
handles.asm=NET.addAssembly('C:\Program Files\Walabot\WalabotMaker\bin\Win32\WalabotAPI.NET.dll');
handles.API=WalabotAPI_NET.WalabotAPI;
handles.API.SetSettingsFolder('C:\ProgramData\Walabot\WalabotMaker');
handles.API.Disconnect;
handles.API.ConnectAny()
PROF_SENSOR=WalabotAPI_NET.APP_PROFILE.PROF_SENSOR;
FILTER_TYPE_DERIVATIVE=WalabotAPI_NET.FILTER_TYPE.FILTER_TYPE_DERIVATIVE;
handles.API.SetProfile(PROF_SENSOR);
X=inputdlg({'R','Theta','Phi'},'',1,{'10 50 0.1','-20 20 10','-45 45 2'});
handles.Parameters.R=str2num(X{1});
handles.Parameters.Theta=str2num(X{2});
handles.Parameters.Phi=str2num(X{2});
handles.API.SetArenaR(handles.Parameters.R(1),handles.Parameters.R(2),handles.Parameters.R(3));
handles.API.SetArenaTheta(handles.Parameters.Theta(1),handles.Parameters.Theta(2),handles.Parameters.Theta(3));
handles.API.SetArenaPhi(handles.Parameters.Phi(1),handles.Parameters.Phi(2),handles.Parameters.Phi(3));
handles.API.SetThreshold(15);
filterType =WalabotAPI_NET.FILTER_TYPE.FILTER_TYPE_NONE;
handles.API.SetDynamicImageFilter(filterType);
handles.API.Start();
handles.API.StartCalibration();
sound_file_name={}; % Complete Sound paths
for i=1:12
    eval(sprintf('[music_%d,fs_%d]=audioread(%s)',i,i,sound_file_name{i}));
end
while (true)
    handles.API.GetStatus();
    handles.API.Trigger();
    targets=handles.API.GetSensorTargets();
    if targets.Length>=1
        region_1=check_region(target(1));
        if targets.Length>1
            region_2=check_region(target(2));
        else
            region_2=0;
        end
    else
        target.xPosCm=0;
        target.yPosCm=0;
        target.zPosCm=0;
        target.amplitude=0;
        region_1=0;
        region_2=0;
    end
    
    if (region_1==0 || region_2==0)
        for i=6:17
            eval(sprintf('set(handles.text%d,''BackgroundColor'',[0.494,0.494,0.494]);',i));
        end
    else
        if region_1~=0
            eval(sprintf('set(handles.text%d, ''BackgroundColor'' , ''green'')',region_1+5));
        end
        if region_2~=0
            eval(sprintf('set(handles.text%d, ''BackgroundColor'' , ''green'')',region_2+5));
        end
    end
    
    pause(0.01);
    handles.API.GetStatus();
    handles.API.Trigger();
    targets=handles.API.GetSensorTargets();
    if targets.Length>=1
        region_11=check_region(target(1));
        if targets.Length>1
            region_22=check_region(target(2));
        else
            region_22=0;
        end
    else
        target.xPosCm=0;
        target.yPosCm=0;
        target.zPosCm=0;
        target.amplitude=0;
        region_11=0;
        region_22=0;
    end
    if (region_22==region_2 && region_2~=0)
        eval(sprintf('sound(music_%d,fs_%d);',region_2,region_2));
    end
    if (region_11==region_1 && region_1~=0)
        eval(sprintf('sound(music_%d,fs_%d);',region_1,region_1));
    end
    for i=6:17
        eval(sprintf('set(handles.text%d,''BackgroundColor'',[0.494,0.494,0.494]);',i));
    end
    
end







% Choose default command line output for KeyBoard
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);
% UIWAIT makes KeyBoard wait for user response (see UIRESUME)
% uiwait(handles.figure1);

function region=check_region(target)
Ylim=[Const1,Const2];
division=linspace(Const1,Const2,17);
for i=2:17
    if (target.yPosCm>=division(i-1) &&target.yPosCm<=division(i))
        region=i-1;
        return;
    end
end
region=0;


% --- Outputs from this function are returned to the command line.
function varargout = KeyBoard_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
